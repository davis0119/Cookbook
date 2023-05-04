# Cookbook | Docker, Local Kubernetes, CI/CD

Before you get started on this assignment, make sure you've watched the lectures on Kubernetes! Also, make sure to install the requisite components for the assignment:

- [Kind](https://kind.sigs.k8s.io/docs/user/quick-start/#installation)
- [Kubectl](https://kubernetes.io/docs/tasks/tools/install-kubectl/)

## Intro

In lecture, we discussed how Kubernetes can be used to run your Docker containers in production. For this assignment, we'll be using Kind to run a local Kubernetes cluster so that you can get familiar with operating Kubernetes before we try to deploy to the cloud.

### What's Kind?

[Kind](https://kind.sigs.k8s.io/) is a tool that we'll use to run Kubernetes locally on our laptops. Kind works by spinning up each Kubernetes component inside Docker so the cluster is completely separate from the host machine. While there are other tools for local development like [Minikube](https://minikube.sigs.k8s.io/docs/), we choose Kind becuase it's resource-efficient and easy to understand.

### What's Kubectl?

[Kubectl](https://kubernetes.io/docs/reference/kubectl/overview/) is the tool that we use to interactive with the Kubernetes clusters that Kind gives us. While Kind focuses on creating clusters, Kubectl focuses on lettings us tell the clusters what to do in terms of what applications to run, what services to connect, etc.

## Setup

We've provided you with a few new files:

- `docker-compose.yml` - This is a filled-out Compose file that we'll use as our reference how to build our Kubernetes manifests. Our application should behave exactly the same inside Kubernetes as it does when we run `docker-compose up` in this directory (same ports, same responses, etc).
- `web/` - This directory holds the code and Dockerfile for running our FastAPI application.
- `cronjob/` - This directory holds the code and Dockerfile for running our aggregator service
- `templates/` - This directory holds templates that we'll use to show a bender information page

## Cluster Creation

First, let's make a cluster with Kind:

```
$ kind create cluster --name cis188
```

`kind` should propertly set the default Kubernetes context to use the new cluster we just created, but to be sure, let's run this command:

```
kubectl config use-context kind-cis188
```

Now that you've got a cluster, start to play around with it! As a refresher some commands we'll use are:

- `kubectl get <resource> -n <namespace>` - get a list of the specified resource
- `kubectl describe <resource> <resource_id> -n <namespace>` - get a thorough description of the specified resource

Try some of these commands out to get a feel for what the cluster looks like:

- `kubectl get pod`
- `kubectl get pod -n kube-system`
- `kubectl describe pod -n kube-system <pod_name>`

Now that you've got a cluster up, make sure to load in our docker image:

```
$ docker build web -t cis1880-cookbook-web:v1
$ kind load docker-image cis1880-cookbook-web:v1 --name cis188
```

This command loads in our FastAPI image to the Docker registry that Kind creates for our cluster so that nodes in our cluster can access it.

## Writing Kubernetes Manifests

In `k8s/redis.yaml` and `k8s/web.yaml`, we've got two blank files. Fill them in such that you have, in total:

- A deployment for the FastAPI server with the name `web` in `web.yaml`
- A service for the FastAPI server on port 8000 with the name `web` in `web.yaml`
- A deployment for the Redis server with the name `redis` in `redis.yaml`
  - Remember that just as in HW1, you'll have to set the `REDIS_URL` environment variable for your fastAPI server to something reasonable. What should it be in Kubernetes?
- A service for the Redis server on port 6379 with the name `redis` in `redis.yaml`

Note that in general, resource names are unique with respect to the resource type and namespace.

Once you've written your manifests, apply them in make sure they spin up!

```
# apply in the manifests
$ kubectl apply -f k8s/
# check their status
$ kubectl get pods
# if a pod is in an error state, describe it to get a more verbose error description
$ kubectl describe pod web-<pod_id>
# check their logs
$ kubectl logs web-<pod_id>
```

If things look good, port forward and curl to test out your server in Kubernetes:

```
# In one terminal
$ kubectl port-forward svc/web 8000:8000

# In another terminal
$ curl -u "blah:blah" 'localhost:8000/hello?name=Ronald'
{"message":"Hello there, Ronald!"}
$ curl -u "blah:blah" -H "Content-Type: application/json" --request POST --data '{"name": "Katara", "element": "water"}' http://localhost:8000/bender
{"message":"Set element for Katara!"}
$ curl -u "blah:blah" 'localhost:8000/bender?name=Katara'
{"name":"Katara","element":"water"}

# For recipes: 
$ curl -u "blah:blah" -H "Content-Type: application/json" --request POST --data '{"name": "spaghetti", "cuisine": "italian", "url": "food.com"}' http://localhost:8000/recipe
$ curl -u "blah:blah" 'localhost:8000/recipe?name=spaghetti'
```

The snippet `-u "blah:blah"` is required because our FastAPI endpoints in this homework are secured with [Basic HTTP Authentication](https://en.wikipedia.org/wiki/Basic_access_authentication). In the last part of the homework we'll add functionality to check for a proper username/password combo, but until then, we can provide any combination we'd like as long as the `Authorization: Basic` header is included with our request.

If these queries work, then congratulations - you've just deployed your first application to Kubernetes!

## Info Page

As of now, we have a way to put our benders into the datastore and a way to get a bender's element out of the datastore, but we have no way to view a list of all our benders. Let's add in an info page so that we can view all the benders!

If you look in `templates/info.html.j2`, you can see we have a [Jinja](https://jinja.palletsprojects.com/en/2.11.x/) template to generate our info page. In `main.py`, we see that our `/info` route expects to find the template at the path `/templates/info.html.j2`. We want to provide the template for this info page at runtime, so instead of packaging the template into the Dockerfile, we're going to use a [ConfigMap](https://kubernetes.io/docs/concepts/configuration/configmap/)!

You should create a ConfigMap in `additional.yaml` named `template-map` with one key, `info.html.j2` whose value is the contents of the info page template.

Once you've written the ConfigMap, modify your `web` deployment spec to mount the info template at `/templates/info.html.j2`.

Now, let's give this a shot! Port forward the `web` service as before, and visit `localhost:8000/info` in your browser. When prompted, enter any username and password combo. If you've mounted your ConfigMap properly, you should see a list of all the benders in your datastore!

If you're getting an internal server error when attempting to visit the page, I'd recommend checking out the logs on your `web-*` pods for more info on what's going wrong.

To make 100% sure things are updating in real-time, use the put bender route to add another bender, refresh the page, and see if the bender has been added!

## Security

Now that we've got our info page, we need to protect this information. Right now, anyone can add benders, get benders, and view our info page. Let's lock this down so that only Avatar Aang can interact with this info.

We've got our FastAPI server set up so that if the `AUTH_REQUIRED` environment variable is set to `true` or `t`, authentication to the server will be required. When the `ADMIN_USERNAME` and `ADMIN_PASSWORD` environment variables are provided, the server will ensure the credentials provided in each request match those present in the environment variables. We'd like for you to use the user `aang` with the password `all4elements`.

To do this, create a [Basic Authentication Secret](https://kubernetes.io/docs/concepts/configuration/secret/#basic-authentication-secret) in `additional.yaml` named `web-secret` with the proper username and password and pass it in as an environment variable to your deployment. Apply your manifests and see if things worked!

Let's test out our routes:

```
# in one terminal
$ kubectl port-forward svc/web 8000:8000

# in another terminal
# unauthenticated request should fail
$ curl -u 'blah:blah' 'localhost:8000/bender?name=toph'
{"detail":"Incorrect email or password"}
# authenticated request should work
$ curl -u 'aang:all4elements' 'localhost:8000/bender?name=toph'
{"name":"toph","element":"earth"}
```

Finally, go to `localhost:8000/info` in your browser and log in to see your benders!


## Aggregation

Now that we've got a secure info page for Aang to look at, his demands have only grown. As he attempts to restore balance, he needs to know which types of benders are most in danger! Aang wants to know which elements are in our datastore as well as how many benders are associated with those elements.

Luckily, we've provided the code and a Dockerfile to do that in the `cronjob` directory. You should write a [Kubernetes CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/) named `aggregator` in `cronjob.yaml` to run the code once per minute. Make sure that you keep around exactly one successful job and one failed job. This is so in the case of a success, we can see the logs of the pod to get our answer, and in the case of a failed job, we can see the logs to see what went wrong.

Make sure to build and name the aggregator image as `hw2-aggregator:v1`

You should also ensure that if a job created by your CronJob fails, the pod created by the CronJob should not restart.

Once you've applied in your CronJob, wait a minute and then check the logs of the Pod that the job spawns:

```
$ kubectl get pod | grep aggregator       
aggregator-1613882400-bprxb   0/1     Completed   0          22s
# Your output will depend on what benders you've put into the dictionary. Just make sure it makes sense!
$ kubectl logs aggregator-1613882400-bprxb
{'earth': 2, 'water': 1}
```

### A note on implementation

It's probably clear here that the work this aggregator's doing is fairly trivial. There's no real reason we couldn't make this a simple route as there aren't that many keys in the datastore, and the transformation is very easy. However, once we start storing more keys and doing more complex transformations, it no longer makes sense to process this data on-request. This is where the value of the CronJob (and Job) shines as we can do the work on a more relaxed schedule and simply check the output.

## Conclusion

To recap, we have:

1. Deployed our application to Kubernetes
2. Connected it to Redis to store data
3. Dynamically passed in a template with a ConfigMap
4. Added in secret-based authentication
5. Bender aggregation with a Cronjob

Here, Kubernetes has allowed us to easily create an application architecture, modify it, and secure it. What's even cooler is that all of our infrastructure could go down, and we're one `kubectl apply -f` away from getting our whole application architecture back.

### [20 points] Extra Credit - Ingresses

In production, we don't use `kubectl port-forward` to access our services. We publish them on public domain names and add configuration to send requests to those domains to our application. We do this via [Ingresses](https://kubernetes.io/docs/concepts/services-networking/ingress/). Using an ingress requires both installing an [Ingress controller](https://kubernetes.io/docs/concepts/services-networking/ingress-controllers/) in our cluster and creating an `Ingress` API object.

For this extra credit, install an Ingress controller of your choice (We recommend [Traefik](https://traefik.io/)) in your cluster. Then, configure add an ingress for FastAPI so that you can go to `localhost:8081` in your browser and get FastAPI. This should happen without any use of `kubectl port-forward`.

Put any Kube configuration you needed for this in `k8s/extracredit/` and a README describing what you did in `k8s/extracredit/README.md`. Best of luck!

Hint: You might need to configure Kind to expose `8081` on your machine before the Ingress controller can receive requests.

## Cleanup

After you've finished this homework assignment, you can delete your kind cluster by running:

```
kind delete cluster --name cis188
```

## Submitting

To submit your homework assignment, just run `make zip` in this repository and upload the resulting zip to Gradescope.

<!-- Copyright CIS 188: Armaan Tobaccowalla & Peyton Walters -->
<!-- 8wMNcOiv45lLUk6AzCKkaL9nLrP9Grkd -->
